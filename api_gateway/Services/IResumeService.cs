namespace api_gateway.Services;

public interface IResumeService
{
    public Task<string> upload (IFormFile resume);
}