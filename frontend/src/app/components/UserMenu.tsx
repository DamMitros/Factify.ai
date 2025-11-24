"use client";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser } from "@fortawesome/free-solid-svg-icons";
import { useState } from "react";
import Link from "next/link";

export default function UserMenu() {
    const [isOpen, setIsOpen] = useState(false);

    const handleLogout = () => {
        setIsOpen(false);
    };

    return (
        <div className="UserMenu">
            <button 
                className="UserIconContainer"
                onClick={() => setIsOpen(!isOpen)}
            >   
                <FontAwesomeIcon icon={faUser} className="UserIcon"/>
            </button>
            
            {isOpen && (
                <div className="UserDropdown">
                    <Link href="/profile" className="UserDropdownItem">Profil</Link>
                    <Link href="/settings" className="UserDropdownItem">Ustawienia</Link>
                    <Link href="/" className="UserDropdownItem" onClick={handleLogout}>Wyloguj</Link>
                </div>
            )}
        </div>
    );
}
