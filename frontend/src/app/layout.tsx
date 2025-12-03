import NavBar from "./components/NavBar";
import "./globals.css";
import KeycloakProviderWrapper from "../auth/KeycloakProviderWrapper";
import { display } from "html2canvas/dist/types/css/property-descriptors/display";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <meta charSet="UTF-8" />
        <link rel="icon" type="image/svg+xml" href="/vite.svg" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Vite + TS</title>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Dongle:wght@700&display=swap" rel="stylesheet" />
      </head>
      <body>
        <KeycloakProviderWrapper>
          {children}

          <NavBar />

          <svg xmlns="http://www.w3.org/2000/svg" style={{ position: "absolute", width: 0, height: 0 }}>
            <defs>
              
              <filter id="goosoft" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur in="SourceGraphic" stdDeviation="14" result="blur" />
                <feColorMatrix in="blur" mode="matrix" values="
                  1 0 0 0 0
                  0 1 0 0 0
                  0 0 1 0 0
                  0 0 3 1 -8" result="goo" />
                <feBlend in="SourceGraphic" in2="goo" />
              </filter>

              <filter id="gooLamp" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur in="SourceGraphic" stdDeviation="22" result="blur" />
                <feColorMatrix in="blur" mode="matrix" values="
                    1 0 0 0 0
                    0 1 0 0 0
                    0 0 1 0 0
                    3 0 0 16 -7" result="goo" />
                <feBlend in="SourceGraphic" in2="goo" />
              </filter>


            </defs>
          </svg>
          <svg xmlns="http://www.w3.org/2000/svg" style={{ position: "absolute", width: 0, height: 0 }}>
            <defs>
              <filter id="lensFilter" x="0%" y="0%" width="100%" height="100%" filterUnits="objectBoundingBox">
                <feComponentTransfer in="SourceAlpha" result="alpha">
                  <feFuncA type="identity" />
                </feComponentTransfer>
      
                <feGaussianBlur in="alpha" stdDeviation="50" result="blur" />

                <feDisplacementMap
                  in="SourceGraphic"
                  in2="blur"
                  scale="50"
                  xChannelSelector="A"
                  yChannelSelector="A"
                />
              </filter>
            </defs>
          </svg>
        </KeycloakProviderWrapper>
      </body>
    </html>
  );
}
