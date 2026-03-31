import { useState } from "react"
import { useNavigate } from "react-router-dom"

import { API, readApiError } from "../api"

function Login() {

    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")
    const [isSubmitting, setIsSubmitting] = useState(false)

    const navigate = useNavigate()

    const login = async () => {
        setError("")

        if (!username.trim() || !password.trim()) {
            setError("Please enter both username and password.")
            return
        }

        setIsSubmitting(true)

        try {
            const form = new URLSearchParams()

            form.append("username", username.trim())
            form.append("password", password)

            const res = await fetch(API + "/auth/token", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: form
            })

            if (!res.ok) {
                const message = await readApiError(res, "Login failed. Please check your credentials.")
                setError(message)
                return
            }

            const data = await res.json()
            localStorage.setItem("token", data.access_token)

            navigate("/products")
        } catch {
            setError("Unable to reach the server. Please try again.")
        } finally {
            setIsSubmitting(false)
        }
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

            {error ? <p className="form-message error-message">{error}</p> : null}

            <button onClick={login} disabled={isSubmitting}>
                {isSubmitting ? "Signing in..." : "Login"}
            </button>

        </div>

    )

}

export default Login