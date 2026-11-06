using System.Text;
using RabbitMQ.Client;

namespace api_gateway.Services;

public sealed class RabbitMqJobPublisher : IJobPublisher
{
    private readonly string _hostName;
    private readonly string _userName;
    private readonly string _password;
    private readonly string _queueName;

    public RabbitMqJobPublisher(IConfiguration configuration)
    {
        _hostName = configuration["RabbitMQ:HostName"] ?? "localhost";

        //TODO: 
        _userName = configuration["RabbitMQ:UserName"] ?? "guest";
        _password = configuration["RabbitMQ:Password"] ?? "guest";
        _queueName = configuration["RabbitMQ:QueueName"] ?? "resume_analysis";
    }

    public async Task PublishAsync(string jobId, CancellationToken cancellationToken)
    {
        var factory = new ConnectionFactory
        {
            HostName = _hostName,
            UserName = _userName,
            Password = _password
        };

        await using var connection = await factory.CreateConnectionAsync(cancellationToken);
        await using var channel = await connection.CreateChannelAsync(cancellationToken: cancellationToken);

        await channel.QueueDeclareAsync(
            queue: _queueName,
            durable: true,
            exclusive: false,
            autoDelete: false,
            arguments: null,
            cancellationToken: cancellationToken);

        var body = Encoding.UTF8.GetBytes(jobId);
        var properties = new BasicProperties { Persistent = true, ContentType = "text/plain" };

        await channel.BasicPublishAsync(
            exchange: string.Empty,
            routingKey: _queueName,
            mandatory: true,
            basicProperties: properties,
            body: body,
            cancellationToken: cancellationToken);

        // TODO: Add logging for successful publishing
        // TODO: Add error throwing
    }
}
