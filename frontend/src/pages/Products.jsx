import { useEffect, useState } from "react"

import { API, readApiError } from "../api"

function Products() {

    const [products, setProducts] = useState([])

    const [name, setName] = useState("")
    const [description, setDescription] = useState("")
    const [price, setPrice] = useState("")
    const [stock, setStock] = useState("")
    const [error, setError] = useState("")
    const [success, setSuccess] = useState("")
    const [isSubmitting, setIsSubmitting] = useState(false)

    const loadProducts = async () => {
        try {
            const res = await fetch(API + "/products")
            if (!res.ok) {
                const message = await readApiError(res, "Failed to load products.")
                setError(message)
                return
            }

            const data = await res.json()
            setProducts(data)
        } catch {
            setError("Unable to load products. Please try again.")
        }
    }

    useEffect(() => {
        loadProducts()
    }, [])

    const addProduct = async () => {
        setError("")
        setSuccess("")

        if (!name.trim()) {
            setError("Product name is required.")
            return
        }

        if (price === "" || stock === "") {
            setError("Price and stock are required.")
            return
        }

        setIsSubmitting(true)

        try {
            const res = await fetch(API + "/products", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name,
                    description,
                    price: Number(price),
                    stock: Number(stock)
                })
            })

            if (!res.ok) {
                const message = await readApiError(res, "Failed to create the product.")
                setError(message)
                return
            }

            setName("")
            setDescription("")
            setPrice("")
            setStock("")
            setSuccess("Product created successfully.")
            await loadProducts()
        } catch {
            setError("Unable to reach the server. Please try again.")
        } finally {
            setIsSubmitting(false)
        }
    }

    const deleteProduct = async (id) => {
        setError("")
        setSuccess("")

        try {
            const res = await fetch(API + "/products/" + id, {
                method: "DELETE"
            })

            if (!res.ok) {
                const message = await readApiError(res, "Failed to delete the product.")
                setError(message)
                return
            }

            setSuccess("Product deleted successfully.")
            await loadProducts()
        } catch {
            setError("Unable to reach the server. Please try again.")
        }
    }

    return (

        <>
            <div className="topbar">
                Online Shop Admin
            </div>

            <div className="container">

                <h1>Products</h1>

                <div className="form">

                    <input placeholder="name" onChange={(e) => setName(e.target.value)} />

                    <input placeholder="description" onChange={(e) => setDescription(e.target.value)} />

                    <input placeholder="price" onChange={(e) => setPrice(e.target.value)} />

                    <input placeholder="stock" onChange={(e) => setStock(e.target.value)} />

                    <button onClick={addProduct} disabled={isSubmitting}>
                        {isSubmitting ? "Saving..." : "Add product"}
                    </button>

                </div>

                {error ? <p className="form-message error-message">{error}</p> : null}
                {success ? <p className="form-message success-message">{success}</p> : null}


                <div className="grid">

                    {products.map(p => (

                        <div className="card" key={p.id}>

                            <h3>{p.name}</h3>

                            <p>{p.description}</p>

                            <p><b>Price:</b> {p.price}</p>

                            <p><b>Stock:</b> {p.stock}</p>

                            <button
                                className="delete"
                                onClick={() => deleteProduct(p.id)}
                            >
                                Delete
                            </button>

                        </div>

                    ))}

                </div>

            </div>
        </>

    )
}

export default Products