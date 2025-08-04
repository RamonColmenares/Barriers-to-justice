# Deployment Instructions

## Contact Form with Email Service

This deployment now includes AWS SES (Simple Email Service) integration for the contact form functionality.

### Quick Deployment

```bash
# Deploy with email parameter
./deploy.sh --email your-email@domain.com

# Or using short flag
./deploy.sh -e your-email@domain.com
```

### What the email is used for:

1. **AWS SES Configuration**: Sets up Simple Email Service to send contact form emails
2. **Let's Encrypt SSL Certificates**: Required for HTTPS certificate registration
3. **Contact Form Backend**: Configures the API to send emails when users submit the contact form

### Email Verification

After deployment:

1. **Check your email inbox** for an AWS SES verification email
2. **Click the verification link** to activate email sending
3. **Test the contact form** on your website

### Email Service Features

- ✅ Contact form submissions sent to your email
- ✅ HTML and plain text email formats
- ✅ Input validation and sanitization
- ✅ Professional email templates
- ✅ Error handling and user feedback

### Environment Variables

The script will:
- Use the `--email` parameter if provided
- Fall back to `$CONTACT_EMAIL` environment variable
- Load from `~/.juvenile_api_deploy` file if available
- Prompt interactively if none of the above

### API Endpoints

After deployment, the contact form API will be available at:
```
POST https://your-domain.sslip.io/api/contact
```

### Troubleshooting

If emails aren't working:
1. Check that you verified your email in AWS SES
2. Ensure your AWS region supports SES (us-east-1 is used by default)
3. Check the Docker container logs: `docker logs juvenile-api`

### Security Notes

- Emails are sent via AWS SES with proper IAM roles
- No email credentials are stored in the code
- Contact form includes validation and rate limiting
- SSL/TLS encryption for all email communications
