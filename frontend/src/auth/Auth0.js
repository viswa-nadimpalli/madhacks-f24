import React from 'react';
import { Auth0Provider } from '@auth0/auth0-react';

const Auth0 = ({ children }) => {
  const domain = process.env.REACT_APP_AUTH0_DOMAIN;
  const clientId = process.env.REACT_APP_AUTH0_CLIENT_ID;

  return (
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirectUri: window.location.origin
      }}
    >
      {children}
    </Auth0Provider>
  );
};

export default Auth0;
