output "acm_validation_records" {
  description = "Add these CNAME records to your DNS provider to validate the ACM certificate. Apply will block until validation completes."
  value = {
    for dvo in aws_acm_certificate.auth_domain.domain_validation_options : dvo.domain_name => {
      name  = dvo.resource_record_name
      type  = dvo.resource_record_type
      value = dvo.resource_record_value
    }
  }
}

output "cognito_cloudfront_domain" {
  description = "Add a CNAME record: auth.syntacticallysugary.dev → this value."
  value       = aws_cognito_user_pool_domain.custom.cloudfront_distribution
}

output "tutor_client_id" {
  description = "New PKCE client ID for Know-It-All Tutor. Update VITE_COGNITO_CLIENT_ID in the Tutor app."
  value       = aws_cognito_user_pool_client.tutor.id
}

output "reading_client_id" {
  description = "New PKCE client ID for Private Reading. Update CONFIG.COGNITO_CLIENT_ID in spa/app.js."
  value       = aws_cognito_user_pool_client.reading.id
}

output "auth_domain" {
  description = "Cognito Hosted UI base URL. Used in app OAuth configs."
  value       = "https://${var.auth_domain}"
}
