function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('main section').forEach(section => {
        section.classList.add('hidden');
    });

    // Show the selected section
    document.getElementById(sectionId).classList.remove('hidden');
}

// Navigate to the /account URL when the Account menu item is clicked
function navigateToAccount() {
    window.location.href = '/account';
}

// Navigate to the / URL when the Wallet menu item is clicked
function navigateToWallet() {
    window.location.href = '/';
}
