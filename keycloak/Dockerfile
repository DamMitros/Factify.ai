FROM quay.io/keycloak/keycloak:26.0.0

COPY keycloak/factify.json /opt/keycloak/data/import/

CMD ["start-dev", "--verbose", "--import-realm"]
