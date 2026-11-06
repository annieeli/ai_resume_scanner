using Microsoft.AspNetCore.Mvc;
using api_gateway.Services;

namespace api_gateway.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ResumeController : ControllerBase
{
    private readonly IResumeService _resumeService;
    public ResumeController(IResumeService resumeService)
    {
        _resumeService = resumeService;
    }

    [HttpPost]
    public async Task<IActionResult> UploadResume(
        [FromForm] IFormFile? resume,
        [FromForm] string? jobDescription,
        CancellationToken cancellationToken)
    {
        if(resume == null || resume.Length == 0)
        {
            return BadRequest("No file uploaded.");
        }

        // TODO: strong validation for file type and size
        var fileExtension = Path.GetExtension(resume.FileName).ToLowerInvariant();
        if(fileExtension != ".pdf")
        {
            return BadRequest("Invalid file type. Only PDF is allowed.");
        }

        if (string.IsNullOrWhiteSpace(jobDescription))
        {
            return BadRequest("A job description is required.");
        }

        var jobId = await _resumeService.UploadAsync(resume, jobDescription, cancellationToken);

        return Accepted(new { JobId = jobId });
    }
}
