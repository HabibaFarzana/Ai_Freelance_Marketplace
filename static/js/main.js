document.addEventListener('DOMContentLoaded', function() {
    // Dynamic pricing suggestion
    const bidForm = document.getElementById('bid-form');
    const bidAmountInput = document.getElementById('id_amount');
    const suggestedPriceSpan = document.getElementById('suggested-price');

    if (bidForm && bidAmountInput && suggestedPriceSpan) {
        const projectId = bidForm.dataset.projectId;
        fetch(`/api/projects/${projectId}/get_price_recommendation/`)
            .then(response => response.json())
            .then(data => {
                suggestedPriceSpan.textContent = `$${data.price_recommendation.toFixed(2)}`;
            });

        bidAmountInput.addEventListener('input', function() {
            const currentBid = parseFloat(this.value);
            const suggestedPrice = parseFloat(suggestedPriceSpan.textContent.slice(1));
            if (currentBid < suggestedPrice * 0.8) {
                this.classList.add('is-invalid');
            } else {
                this.classList.remove('is-invalid');
            }
        });
    }

    // Real-time work monitoring (simplified version)
    const workMonitoringBtn = document.getElementById('start-monitoring');
    if (workMonitoringBtn) {
        workMonitoringBtn.addEventListener('click', function() {
            // In a real implementation, this would start capturing screenshots or tracking activity
            console.log('Work monitoring started');
            this.textContent = 'Monitoring...';
            this.disabled = true;
        });
    }

    // Project matching
    const matchProjectBtn = document.getElementById('match-project');
    const matchResultsDiv = document.getElementById('match-results');
    if (matchProjectBtn && matchResultsDiv) {
        matchProjectBtn.addEventListener('click', function() {
            const projectId = this.dataset.projectId;
            fetch(`/api/projects/${projectId}/match_freelancers/`)
                .then(response => response.json())
                .then(data => {
                    matchResultsDiv.innerHTML = '<h4>Top Matches:</h4>';
                    data.forEach(freelancer => {
                        matchResultsDiv.innerHTML += `
                            <div class="card mb-2">
                                <div class="card-body">
                                    <h5 class="card-title">${freelancer.username}</h5>
                                    <p class="card-text">${freelancer.bio}</p>
                                    <a href="/profiles/${freelancer.id}" class="btn btn-primary btn-sm">View Profile</a>
                                </div>
                            </div>
                        `;
                    });
                });
        });
    }
});