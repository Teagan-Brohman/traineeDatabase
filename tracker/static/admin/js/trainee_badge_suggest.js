(function() {
    'use strict';

    // Wait for Django admin to be ready
    if (typeof django === 'undefined' || !django.jQuery) {
        // Fallback to native DOMContentLoaded if Django admin jQuery not available
        document.addEventListener('DOMContentLoaded', initBadgeSuggest);
    } else {
        django.jQuery(document).ready(initBadgeSuggest);
    }

    function initBadgeSuggest() {
        var cohortField = document.getElementById('id_cohort');
        var badgeField = document.getElementById('id_badge_number');

        if (!cohortField || !badgeField) {
            return; // Fields not found on this page
        }

        // Only auto-suggest for new trainees (empty badge number)
        if (badgeField.value && badgeField.value.trim() !== '') {
            return; // Editing existing trainee, don't override
        }

        // Add event listener for cohort changes
        cohortField.addEventListener('change', function() {
            updateBadgeSuggestion();
        });

        // Initial suggestion if cohort already selected
        if (cohortField.value) {
            updateBadgeSuggestion();
        }

        function updateBadgeSuggestion() {
            var cohortId = cohortField.value;

            if (!cohortId) {
                badgeField.placeholder = 'Select cohort first';
                return;
            }

            // Get cohort info from the select option
            var selectedOption = cohortField.options[cohortField.selectedIndex];
            var cohortName = selectedOption.text;

            // Extract year from cohort name (e.g., "Fall 2025" -> "2025")
            var yearMatch = cohortName.match(/\d{4}/);
            if (!yearMatch) {
                badgeField.placeholder = 'Unable to detect year from cohort';
                return;
            }

            var fullYear = yearMatch[0];
            var shortYear = fullYear.slice(-2); // Last 2 digits

            // Make AJAX request to get next badge number
            fetch('/admin/tracker/trainee/get-next-badge/' + cohortId + '/')
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(function(data) {
                    if (data.next_badge) {
                        badgeField.value = data.next_badge;
                        badgeField.placeholder = 'Suggested: ' + data.next_badge;

                        // Add visual feedback
                        badgeField.style.backgroundColor = '#e8f5e9';
                        setTimeout(function() {
                            badgeField.style.backgroundColor = '';
                        }, 1000);
                    }
                })
                .catch(function(error) {
                    console.log('Error fetching badge suggestion:', error);
                    // Fallback: just show expected format
                    badgeField.placeholder = 'Format: #' + shortYear + 'XX (e.g., #' + shortYear + '01)';
                });
        }

        // Add help text below the field
        var helpText = document.createElement('p');
        helpText.className = 'help';
        helpText.style.color = '#666';
        helpText.textContent = 'Badge number will auto-suggest when you select a cohort';

        var badgeFieldParent = badgeField.parentNode;
        if (badgeFieldParent && !badgeFieldParent.querySelector('.help')) {
            badgeFieldParent.appendChild(helpText);
        }
    }
})();
