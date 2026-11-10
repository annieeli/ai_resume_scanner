namespace api_gateway.Services;

using System.Text.Json;

public class ResumeService : IResumeService
{
    private readonly string _storageRoot;
    private readonly IJobPublisher _jobPublisher;

    public ResumeService(IConfiguration configuration, IJobPublisher jobPublisher)
    {
        _storageRoot = configuration["Storage:RootPath"] ?? throw new ArgumentNullException("Storage:RootPath configuration is missing.");
        _jobPublisher = jobPublisher ?? throw new ArgumentNullException(nameof(jobPublisher));
    }

    public async Task<string> UploadAsync (IFormFile resume, string jobDescription, CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested();

        var jobId = Guid.NewGuid().ToString();
        var jobDirectory = Path.Combine(_storageRoot, jobId);

        //store info to local storage for worker to access (later change to store to s3)
        Directory.CreateDirectory(jobDirectory);

        //store resume
        var resumePath = Path.Combine(jobDirectory, "resume.pdf");
        await using (var stream = new FileStream(resumePath, FileMode.CreateNew))
        {
            await resume.CopyToAsync(stream, cancellationToken);
        }

        //store job description
        var jobDescriptionPath = Path.Combine(jobDirectory, "job_description.txt");
        await File.WriteAllTextAsync(jobDescriptionPath, jobDescription, cancellationToken);

        //store job.json (jobId and status)
        var metadata = new JobMetaData(
            jobId,
            "Queued",
            $"{jobId}/resume.pdf",
            $"{jobId}/job_description.txt"
        ); 

        var jobJsonPath = Path.Combine(jobDirectory, "job.json");
        await WriteMetadataAsync(jobJsonPath, metadata, cancellationToken);
        
        // publish to rabbitmq
        await _jobPublisher.PublishAsync(jobId, cancellationToken);

        return jobId;
    }

    private record JobMetaData(string JobId, string Status, string ResumePath, string JobDescriptionPath);

    private static Task WriteMetadataAsync(string path, JobMetaData metadata, CancellationToken cancellationToken)
    {
        var json = JsonSerializer.Serialize(metadata);
        return File.WriteAllTextAsync(path, json, cancellationToken);
    }
}