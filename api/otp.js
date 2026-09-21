export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({
      error: "method_not_allowed"
    });
  }

  try {
    const token = req.headers.authorization
      ?.replace(/^Bearer\s+/i, "");

    const { accountId } = req.body || {};

    if (!token || !accountId) {
      return res.status(400).json({
        error: "missing_token_or_account_id"
      });
    }

    const response = await fetch(
      `https://api.derivws.com/trading/v1/options/accounts/${encodeURIComponent(accountId)}/otp`,
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      }
    );

    const data = await response.json();

    res.setHeader("Cache-Control", "no-store");

    return res.status(response.status).json(data);

  } catch (error) {
    return res.status(500).json({
      error: "otp_request_failed",
      message: error.message
    });
  }
}
