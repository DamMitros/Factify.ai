import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser } from "@fortawesome/free-solid-svg-icons";
import UserMenu from "./UserMenu";


export default function NavBar() {
    return (
        <nav className="GlobalNav">
            <UserMenu />
        </nav>
    );
}
