//get from user
//post/post to handle
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
    public IActionResult UploadResume([FromForm] IFormFile resume)
    {
        if(resume == null || resume.Length == 0)
        {
            return BadRequest("No file uploaded.");
        }

        var allowedExtensions = new[] { ".pdf", ".doc", ".docx" };
        var fileExtension = Path.GetExtension(resume.FileName).ToLowerInvariant();
        if(!allowedExtensions.Contains(fileExtension))
        {
            return BadRequest("Invalid file type. Only PDF, DOC, and DOCX are allowed.");
        }

        var jobId = _resumeService.upload(resume);

        return Accepted(new{JobId = jobId});
    }
}
