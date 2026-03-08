import { useState } from "react"
import { useNavigate } from "react-router-dom"

const API = "http://localhost:8000"

function Login() {

    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")

    const navigate = useNavigate()

    const login = async () => {

        const form = new URLSearchParams()

        form.append("username", username)
        form.append("password", password)

        const res = await fetch(API + "/auth/token", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: form
        })

        const data = await res.json()

        localStorage.setItem("token", data.access_token)

        navigate("/products")
    }

    return (

        <div style={{ padding: "40px" }}>

            <h1>Login</h1>

            <input
                placeholder="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />

            <input
                type="password"
                placeholder="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />

            <button onClick={login}>Login</button>

        </div>

    )

}

export default Login