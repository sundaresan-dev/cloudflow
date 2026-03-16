// Hotel management functionality

document.addEventListener('DOMContentLoaded', () => {
    console.log('Hotel Management System loaded');
    
    // Booking form functionality
    const bookingForm = document.querySelector('.booking-form form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', (e) => {
            e.preventDefault();
            alert('Thank you for your booking request! Our team will contact you soon.');
        });
    }
    
    // Book button functionality
    const bookButtons = document.querySelectorAll('.room-card .btn-primary');
    bookButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const roomCard = e.target.closest('.room-card');
            if (roomCard) {
                const roomName = roomCard.querySelector('h4').textContent;
                alert(`Room "${roomName}" has been added to your cart!`);
            }
        });
    });
});
