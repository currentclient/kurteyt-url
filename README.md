# kurteyt-url

A url shortener using Fastapi on lambda, dynamodb, and cloudfront.

## Notes

- Lambda at edge logs will be recorded in each region (edge) where the viewer made the request

## &#x1F4DA; Developer Reference

- [Serverless http api](https://www.serverless.com/framework/docs/providers/aws/events/http-api/)
- [Serverless dot env](https://github.com/neverendingqs/serverless-dotenv-plugin)
- [Mangum (ASGI)](https://mangum.io/)
- [Lamdba@edge for requests](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-generating-http-responses-in-requests.html)
- [Lamdba@edge event structure](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/lambda-event-structure.html#example-viewer-request)
- [Lamdba@edge example walkthrough](https://making.close.com/posts/redirects-using-cloudfront-lambda-edge)
