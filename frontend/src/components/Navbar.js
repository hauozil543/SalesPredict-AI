import React from "react";
import { Link } from "react-router-dom";

function Navbar() {
    return (
        <nav>
            <ul>
                <li><Link to="/">Home</Link></li>
                <li><Link to="/forecast">Forecast</Link></li>
                <li><Link to="/results">Results</Link></li>
            </ul>
        </nav>
    );
}

export default Navbar;
