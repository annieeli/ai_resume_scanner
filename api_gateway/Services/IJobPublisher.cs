namespace api_gateway.Services;

public interface IJobPublisher
{
    Task PublishAsync(string jobId, CancellationToken cancellationToken);
}
