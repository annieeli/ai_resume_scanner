namespace api_gateway.Services;

public class ResumeService : IResumeService
{
    public async Task<string> upload (IFormFile resume)
    {
        var jobId = Guid.NewGuid().ToString();

        //store pdf to local for worker to access (later change to store to s3)

        //store pdf to db (store the status)

        //publish to rabbitmq

        return jobId;
    }
}