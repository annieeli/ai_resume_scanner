namespace api_gateway.Services;

public interface IResumeService
{
    Task<string> UploadAsync(IFormFile resume, string jobDescription, CancellationToken cancellationToken);
    Task<JobStatus?> GetJobStatusAsync(string jobId, CancellationToken cancellationToken);
}