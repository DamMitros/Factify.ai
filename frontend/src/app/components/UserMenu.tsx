"use client";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser } from "@fortawesome/free-solid-svg-icons";
import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useKeycloak } from "../../auth/KeycloakProviderWrapper";
import LoginButton from "./LoginButton";
import RegisterButton from "./RegisterButton";

export default function UserMenu() {
    const [isOpen, setIsOpen] = useState(false);
    const { keycloak, authenticated, initialized } = useKeycloak();
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        if (isOpen) {
            document.addEventListener('mousedown', handleClickOutside);
        }

        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isOpen]);

    const handleLogout = () => {
        if (!keycloak) return;
        keycloak.logout({ redirectUri: "http://localhost:3000" });
        setIsOpen(false);
    };

    if (!initialized) {
        return null;
    }

    return (
        <div className="UserMenu" ref={menuRef}>
            <button 
                className="UserIconContainer"
                onClick={() => setIsOpen(!isOpen)}
            >   
                <FontAwesomeIcon icon={faUser} className="UserIcon"/>
            </button>
            
            {isOpen && (
                <div className="UserDropdown">
                    {authenticated ? (
                        <>
                            <Link href="/profile" className="UserDropdownItem" onClick={() => setIsOpen(false)}>
                                Analyze History
                            </Link>
                            { (keycloak?.hasRealmRole("admin")) && (
                                <Link href="/admin" className="UserDropdownItem" onClick={() => setIsOpen(false)}>
                                    Admin Panel
                                </Link>
                            )}
                            <button className="UserDropdownItem" onClick={handleLogout}>
                                Log out
                            </button>
                        </>
                    ) : (
                        <>
                            <div className="UserDropdownItem">
                                <LoginButton />
                            </div>
                            {/* <div className="UserDropdownItem">
                                <RegisterButton />
                            </div> */}
                        </>
                    )}
                </div>
            )}
        </div>
    );
}
