export default function Bubbles() {
    return (
        <>
            <svg xmlns="http://www.w3.org/2000/svg" style={{ position: "fixed", width: 0, height: 0 }}>
                <defs>
                    <filter id="goo">
                        <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
                        <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -8" result="goo" />
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
                

                <feGaussianBlur in="alpha" stdDeviation="40" result="blur" />

                <feDisplacementMap
                  in="SourceGraphic"
                  in2="blur"
                  scale="100"
                  xChannelSelector="A"
                  yChannelSelector="A"
                  
                />
              </filter>
            </defs>
          </svg>
            <div className="bubbles blur-xl ">
                <div className="bubble bubble1"></div>
                <div className="bubble bubble2"></div>
                <div className="bubble bubble3"></div>  
                <div className="bubble bubble4"></div>
                <div className="bubble bubble5"></div>
                <div className="bubble bubble6"></div>
            </div>
        </>
    )

}
