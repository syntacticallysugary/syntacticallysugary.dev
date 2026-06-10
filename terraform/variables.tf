variable "user_pool_id" {
  type        = string
  description = "ID of the Cognito User Pool managed by the Know-It-All CloudFormation stack."
  default     = "us-east-1_Bg1FA4097"
}

variable "auth_domain" {
  type        = string
  description = "Custom domain for the Cognito Hosted UI."
  default     = "auth.syntacticallysugary.dev"
}

variable "tutor_origin" {
  type        = string
  description = "Base URL of the Know-It-All Tutor app."
  default     = "https://tutor.syntacticallysugary.dev"
}

variable "reading_origin" {
  type        = string
  description = "Base URL of the Private Reading app."
  default     = "https://reading.syntacticallysugary.dev"
}
