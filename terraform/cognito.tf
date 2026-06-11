data "aws_cognito_user_pool" "shared" {
  user_pool_id = var.user_pool_id
}

# Custom domain — replaces the private-reading-prod prefix domain.
# Before applying this resource, remove the prefix domain from Private Reading's Terraform:
#   terraform -chdir=../../../myaudible/terraform destroy -target module.cognito.aws_cognito_user_pool_domain.private_reading
resource "aws_cognito_user_pool_domain" "custom" {
  domain          = var.auth_domain
  certificate_arn = aws_acm_certificate_validation.auth_domain.certificate_arn
  user_pool_id    = data.aws_cognito_user_pool.shared.id
}

# Hosted UI appearance — matches syntacticallysugary.dev dark navy theme.
resource "aws_cognito_user_pool_ui_customization" "shared" {
  user_pool_id = data.aws_cognito_user_pool.shared.id

  css = <<-CSS
    .background-customizable {
      background-color: #0f172a;
    }
    .banner-customizable {
      background-color: #0f172a;
      padding: 2rem 0 1rem;
    }
    .label-customizable {
      font-weight: 400;
      color: #94a3b8;
      font-size: 0.875rem;
    }
    .textDescription-customizable {
      color: #94a3b8;
      font-size: 0.875rem;
    }
    .idpDescription-customizable {
      color: #94a3b8;
    }
    .legalText-customizable {
      color: #475569;
      font-size: 0.75rem;
    }
    .submitButton-customizable {
      background-color: #2563eb;
      border: none;
      border-radius: 6px;
      font-size: 0.9rem;
      font-weight: 600;
      padding: 0.65rem 1.25rem;
    }
    .submitButton-customizable:hover {
      background-color: #1d4ed8;
    }
    .errorMessage-customizable {
      background-color: rgba(239, 68, 68, 0.1);
      border: 1px solid rgba(239, 68, 68, 0.3);
      color: #f87171;
      border-radius: 6px;
      padding: 0.75rem 1rem;
    }
    .inputField-customizable {
      background-color: #1e293b;
      border: 1px solid #334155;
      border-radius: 6px;
      color: #f8fafc;
      font-size: 0.9rem;
    }
    .inputField-customizable:focus {
      border-color: #3b82f6;
      outline: none;
    }
    .idpButton-customizable {
      background-color: #1e293b;
      border: 1px solid #334155;
      border-radius: 6px;
      color: #f8fafc;
    }
    .socialButton-customizable {
      background-color: #1e293b;
      border: 1px solid #334155;
      color: #f8fafc;
      border-radius: 6px;
    }
  CSS

  depends_on = [aws_cognito_user_pool_domain.custom]
}

# Know-It-All Tutor — PKCE app client.
# The existing CDK-managed client (6d56bp4dfiu42chkdjjmln6bb9) stays in place during migration.
# Once the Tutor app is updated to use this client ID, the CDK client can be removed.
resource "aws_cognito_user_pool_client" "tutor" {
  name         = "know-it-all-tutor-sso"
  user_pool_id = data.aws_cognito_user_pool.shared.id

  generate_secret = false

  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  supported_identity_providers         = ["COGNITO"]

  explicit_auth_flows = ["ALLOW_REFRESH_TOKEN_AUTH"]

  callback_urls = ["${var.tutor_origin}/callback"]
  logout_urls   = ["${var.tutor_origin}/"]

  access_token_validity  = 60
  id_token_validity      = 60
  refresh_token_validity = 30
  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  prevent_user_existence_errors = "ENABLED"
}

# Private Reading — PKCE app client.
# Replaces the native USER_PASSWORD_AUTH client (7lkv9uvo8e8f47gepa7fg7rbb9).
resource "aws_cognito_user_pool_client" "reading" {
  name         = "private-reading-sso"
  user_pool_id = data.aws_cognito_user_pool.shared.id

  generate_secret = false

  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  supported_identity_providers         = ["COGNITO"]

  explicit_auth_flows = ["ALLOW_REFRESH_TOKEN_AUTH"]

  callback_urls = ["${var.reading_origin}/"]
  logout_urls   = ["${var.reading_origin}/"]

  access_token_validity  = 60
  id_token_validity      = 60
  refresh_token_validity = 30
  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  prevent_user_existence_errors = "ENABLED"
}
