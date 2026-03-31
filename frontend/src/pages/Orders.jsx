import { useState } from "react"

import { API, readApiError } from "../api"

function Orders() {

    const [userId, setUserId] = useState("")
    const [productId, setProductId] = useState("")
    const [quantity, setQuantity] = useState("")
    const [address, setAddress] = useState("")
    const [error, setError] = useState("")
    const [success, setSuccess] = useState("")
    const [isSubmitting, setIsSubmitting] = useState(false)

    const createOrder = async () => {
        setError("")
        setSuccess("")

        if (!userId || !productId || !quantity || !address.trim()) {
            setError("Please fill in all order fields.")
            return
        }

        setIsSubmitting(true)

        try {
            const res = await fetch(API + "/orders", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    user_id: Number(userId),
                    address,
                    items: [
                        {
                            product_id: Number(productId),
                            quantity: Number(quantity)
                        }
                    ]
                })
            })

            if (!res.ok) {
                const message = await readApiError(res, "Failed to create the order.")
                setError(message)
                return
            }

            setUserId("")
            setProductId("")
            setQuantity("")
            setAddress("")
            setSuccess("Order created successfully.")
        } catch {
            setError("Unable to reach the server. Please try again.")
        } finally {
            setIsSubmitting(false)
        }

    }

    return (

        <div style={{ padding: "40px" }}>

            <h1>Create order</h1>

            <input placeholder="user id" onChange={(e) => setUserId(e.target.value)} />

            <input placeholder="product id" onChange={(e) => setProductId(e.target.value)} />

            <input placeholder="quantity" onChange={(e) => setQuantity(e.target.value)} />

            <input placeholder="address" onChange={(e) => setAddress(e.target.value)} />

            {error ? <p className="form-message error-message">{error}</p> : null}
            {success ? <p className="form-message success-message">{success}</p> : null}

            <button onClick={createOrder} disabled={isSubmitting}>
                {isSubmitting ? "Creating..." : "Create order"}
            </button>

        </div>

    )

}

export default Orders