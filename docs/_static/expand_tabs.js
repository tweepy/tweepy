// Source: https://github.com/readthedocs/readthedocs.org/blob/f38fe0f48ed4fcfa715f647bbd073356effbb9ee/docs/_static/js/expand_tabs.js

/*
 * Expands a specific tab of sphinx-tabs.
 * Usage:
 * - docs.readthedocs.io/?tab=Name
 * - docs.readthedocs.io/?tab=Name#section
 * Where 'Name' is the title of the tab (case sensitive).
*/
$( document ).ready(function() {
  const urlParams = new URLSearchParams(window.location.search);
  const tabName = urlParams.get('tab');
  if (tabName !== null) {
    const tab = $('button.sphinx-tabs-tab:contains("' + tabName + '")');
    if (tab.length > 0) {
      tab.click();
    }
  }
});