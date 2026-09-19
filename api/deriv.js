module.exports = async function handler(req, res) {
  const action = new URL(req.url, 'https://local').searchParams.get('action');

  if (action === 'exchange') return exchange(req, res);
  if (action === 'accounts') return accounts(req, res);
  if (action === 'otp') return otp(req, res);
  if (action === 'logout') return logout(req, res);

  return res.status(404).json({ error: 'Unknown action' });
};

async function exchange(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { code, code_verifier, redirect_uri } = req.body || {};

  if (!code || !code_verifier || !redirect_uri) {
    return res.status(400).json({
      error: 'Missing OAuth parameters'
    });
  }

  const clientId = process.env.DERIV_CLIENT_ID;

  if (!clientId) {
    return res.status(500).json({
      error: 'DERIV_CLIENT_ID is not configured'
    });
  }

  const body = new URLSearchParams({
    grant_type: 'authorization_code',
    client_id: clientId,
    code,
    code_verifier,
    redirect_uri
  });

  try {
    const response = await fetch(
      'https://auth.deriv.com/oauth2/token',
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/x-www-form-urlencoded'
        },
        body
      }
    );

    const data = await response.json();

    if (!response.ok || !data.access_token) {
      return res.status(response.status || 400).json({
        error:
          data.error_description ||
          data.error ||
          'Token exchange failed'
      });
    }

    const maxAge = Number(data.expires_in || 3600);

    res.setHeader(
      'Set-Cookie',
      `deriv_access=${encodeURIComponent(
        data.access_token
      )}; Path=/; Max-Age=${maxAge}; HttpOnly; Secure; SameSite=Lax`
    );

    return res.status(200).json({
      ok: true,
      expires_in: maxAge
    });
  } catch (error) {
    return res.status(500).json({
      error: 'OAuth exchange failed'
    });
  }
}

async function accounts(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({
      error: 'Method not allowed'
    });
  }

  const token = getCookie(req, 'deriv_access');

  if (!token) {
    return res.status(401).json({
      error: 'Not authenticated'
    });
  }

  try {
    const response = await fetch(
      'https://api.derivws.com/trading/v1/options/accounts',
      {
        headers: {
          Authorization:
            `Bearer ${decodeURIComponent(token)}`
        }
      }
    );

    const data = await response.json();

    return res.status(response.status).json(data);
  } catch (error) {
    return res.status(502).json({
      error: 'Could not reach Deriv'
    });
  }
}

async function otp(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({
      error: 'Method not allowed'
    });
  }

  const token = getCookie(req, 'deriv_access');

  if (!token) {
    return res.status(401).json({
      error: 'Not authenticated'
    });
  }

  const { account_id } = req.body || {};

  if (!account_id) {
    return res.status(400).json({
      error: 'account_id is required'
    });
  }

  if (!/^[A-Za-z0-9_-]+$/.test(account_id)) {
    return res.status(400).json({
      error: 'Invalid account_id'
    });
  }

  try {
    const response = await fetch(
      `https://api.derivws.com/trading/v1/options/accounts/${encodeURIComponent(
        account_id
      )}/otp`,
      {
        method: 'POST',
        headers: {
          Authorization:
            `Bearer ${decodeURIComponent(token)}`
        }
      }
    );

    const data = await response.json();

    return res.status(response.status).json(data);
  } catch (error) {
    return res.status(502).json({
      error: 'Could not reach Deriv'
    });
  }
}

async function logout(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({
      error: 'Method not allowed'
    });
  }

  res.setHeader(
    'Set-Cookie',
    'deriv_access=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax'
  );

  return res.status(200).json({
    ok: true
  });
}

function getCookie(req, name) {
  const raw = req.headers.cookie || '';

  const found = raw
    .split(';')
    .map(x => x.trim())
    .find(x => x.startsWith(name + '='));

  return found
    ? found.slice(name.length + 1)
    : null;
}
