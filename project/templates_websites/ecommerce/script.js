// E-commerce store functionality

document.addEventListener('DOMContentLoaded', () => {
    console.log('E-commerce store loaded');
    
    // Add to cart functionality
    const addToCartButtons = document.querySelectorAll('.btn-primary');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const productCard = e.target.closest('.product-card');
            if (productCard) {
                const productName = productCard.querySelector('h3').textContent;
                alert(`${productName} added to cart!`);
            }
        });
    });
});
