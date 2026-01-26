FROM quay.io/keycloak/keycloak:26.0.0

COPY keycloak/factify.json /opt/keycloak/data/import/

COPY keycloak/cert.pem /opt/keycloak/conf/cert.pem
COPY keycloak/key.pem /opt/keycloak/conf/key.pem

USER root
RUN chown 1000:1000 /opt/keycloak/conf/cert.pem /opt/keycloak/conf/key.pem

USER 1000

CMD ["start-dev", "--verbose", "--import-realm", "--https-certificate-file=/opt/keycloak/conf/cert.pem", "--https-certificate-key-file=/opt/keycloak/conf/key.pem"]
