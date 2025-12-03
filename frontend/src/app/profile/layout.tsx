import React from "react";

type LayoutProps = {
    children: React.ReactNode;
};

const Layout: React.FC<LayoutProps> = ({ children }) => {
    return (
        <div className="analize-text-layout" style={{ minHeight: "100vh" }}>
            {children}
        </div>
    );
};

export default Layout;
