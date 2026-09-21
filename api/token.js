export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({
      error: "method_not_allowed"
    });
  }

  try {
    const {
      code,
      code_verifier,
      redirect_uri
    } = req.body || {};

    const clientId = process.env.DERIV_CLIENT_ID;
    const registeredRedirect = process.env.DERIV_REDIRECT_URI;

    if (!clientId || !registeredRedirect) {
      return res.status(500).json({
        error: "deriv_oauth_not_configured"
      });
    }

    if (!code || !code_verifier || !redirect_uri) {
      return res.status(400).json({
        error: "missing_oauth_parameters"
      });
    }

    if (redirect_uri !== registeredRedirect) {
      return res.status(400).json({
        error: "redirect_uri_mismatch"
      });
    }

    const body = new URLSearchParams({
      grant_type: "authorization_code",
      client_id: clientId,
      code,
      code_verifier,
      redirect_uri
    });

    const response = await fetch(
      "https://auth.deriv.com/oauth2/token",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body
      }
    );

    const data = await response.json();

    if (!response.ok) {
      return res.status(response.status).json({
        error: "deriv_token_exchange_failed",
        detail: data
      });
    }

    res.setHeader("Cache-Control", "no-store");

    return res.status(200).json({
      access_token: data.access_token,
      token_type: data.token_type,
      expires_in: data.expires_in
    });

  } catch (error) {
    return res.status(500).json({
      error: "token_exchange_error",
      message: error.message
    });
  }
}
