# ACM certificate for auth.syntacticallysugary.dev
# Must be in us-east-1 — Cognito custom domains require a us-east-1 certificate regardless of region.

resource "aws_acm_certificate" "auth_domain" {
  domain_name       = var.auth_domain
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# Waits for the certificate to reach ISSUED status.
# Apply will block here until you add the DNS validation CNAME to your DNS provider.
# The required CNAME record is in the acm_validation_records output.
resource "aws_acm_certificate_validation" "auth_domain" {
  certificate_arn = aws_acm_certificate.auth_domain.arn
}
