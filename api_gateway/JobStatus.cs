namespace api_gateway
{
    public enum JobStatus
    {
        Unknown,
        Queued,
        ExtractingText,
        Analyzing,
        Completed,
        Failed
    }
}