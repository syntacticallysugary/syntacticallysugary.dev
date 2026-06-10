terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0, < 6.0"
    }
  }

  cloud {
    organization = "SyntacticallySugary"

    workspaces {
      name = "shared-auth"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}
