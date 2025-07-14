# Domestic Travel Enhancement

## Overview

This enhancement adds two key features to the domestic travel functionality:

1. **Amount Field Repositioning**: When "Domestic Travel" is selected, the Amount field moves to appear after the Distance field in the travel section
2. **Travel-Only New Expenses**: When the first expense has "Domestic Travel" selected, new expenses added via the "Add Expense" button will show only travel details

## Features Implemented

### 1. Amount Field Repositioning for Domestic Travel

#### What Changed
- Added a new `domestic-amount-row-{expenseId}` field that appears within the travel section
- Modified the standard amount field to have ID `standard-amount-row-{expenseId}` for conditional display
- Updated JavaScript to show/hide appropriate amount fields based on travel type selection

#### How It Works
- **Local Travel**: Shows standard amount field, hides domestic amount field
- **Domestic Travel**: Hides standard amount field, shows domestic amount field after Distance
- **No Travel Type**: Shows standard amount field, hides domestic amount field

#### Code Changes
```javascript
// In travel type change handler
if (travelType === 'domestic') {
    // Hide standard amount field, show domestic amount field
    standardAmountRow.hide();
    domesticAmountRow.show();
    standardAmountInput.prop('required', false);
    domesticAmountInput.prop('required', true);
}
```

### 2. Travel-Only New Expenses

#### What Changed
- Modified the "Add Expense" button logic to detect when first expense has domestic travel
- New expenses automatically show travel fields and set travel type to "domestic"
- Standard expense fields are hidden for new expenses in domestic travel mode

#### How It Works
- When user clicks "Add Expense" button, system checks if first expense has `travelType-1` set to "domestic"
- If domestic travel mode is active:
  - New expense shows travel fields by default
  - Travel type is pre-selected as "domestic"
  - Standard amount field is hidden, domestic amount field is shown
  - KM field is hidden (not needed for domestic travel)
  - Receipt upload is required

#### Code Changes
```javascript
// In addExpenseBtn click handler
const firstExpenseTravelType = $('#travelType-1').val();
const isDomesticTravelMode = firstExpenseTravelType === 'domestic';

if (isDomesticTravelMode) {
    // Hide standard expense fields and show only travel fields
    newExpense.find('#standard-amount-row-' + expenseCount).hide();
    newExpense.find('#domestic-amount-row-' + expenseCount).show();
    // ... additional configuration
}
```

## Technical Implementation

### HTML Structure Changes

#### Original Structure
```html
<!-- Standard amount field -->
<div class="row mb-3">
    <div class="col-12">
        <label for="amount-1">Amount (₹)</label>
        <input type="number" id="amount-1" name="amount[]">
    </div>
</div>

<!-- Travel fields -->
<div class="travel-fields" id="travel-fields-1">
    <!-- Travel type, mode, from, to, date, distance -->
</div>
```

#### New Structure
```html
<!-- Standard amount field (conditionally shown) -->
<div class="row mb-3" id="standard-amount-row-1">
    <div class="col-12">
        <label for="amount-1">Amount (₹)</label>
        <input type="number" id="amount-1" name="amount[]">
    </div>
</div>

<!-- Travel fields -->
<div class="travel-fields" id="travel-fields-1">
    <!-- Travel type, mode, from, to, date, distance -->
    
    <!-- Domestic amount field (conditionally shown) -->
    <div class="row mb-3" id="domestic-amount-row-1" style="display: none;">
        <div class="col-12">
            <label for="domestic-amount-1">Amount (₹)</label>
            <input type="number" id="domestic-amount-1" name="amount[]">
        </div>
    </div>
</div>
```

### JavaScript Changes

#### Travel Type Change Handler
```javascript
$(document).on("change", ".travel-type-select", function() {
    const expenseId = $(this).attr('id').split('-')[1];
    const travelType = $(this).val();
    
    const standardAmountRow = $(`#standard-amount-row-${expenseId}`);
    const domesticAmountRow = $(`#domestic-amount-row-${expenseId}`);
    const standardAmountInput = $(`#amount-${expenseId}`);
    const domesticAmountInput = $(`#domestic-amount-${expenseId}`);
    
    if (travelType === 'domestic') {
        // Show domestic amount, hide standard amount
        standardAmountRow.hide();
        domesticAmountRow.show();
        standardAmountInput.prop('required', false);
        domesticAmountInput.prop('required', true);
    } else {
        // Show standard amount, hide domestic amount
        standardAmountRow.show();
        domesticAmountRow.hide();
        standardAmountInput.prop('required', true);
        domesticAmountInput.prop('required', false);
    }
});
```

#### Add Expense Button Enhancement
```javascript
$("#addExpenseBtn").click(function() {
    // ... existing logic ...
    
    // Check if first expense has domestic travel selected
    const firstExpenseTravelType = $('#travelType-1').val();
    const isDomesticTravelMode = firstExpenseTravelType === 'domestic';
    
    if (isDomesticTravelMode) {
        // Configure new expense for domestic travel mode
        newExpense.find('#standard-amount-row-' + expenseCount).hide();
        newExpense.find('#domestic-amount-row-' + expenseCount).show();
        newExpense.find('#travel-fields-' + expenseCount).show();
        newExpense.find('#travelType-' + expenseCount).val('domestic');
        // ... additional configuration
    }
});
```

### Database Considerations

The existing database structure supports this enhancement without changes:
- Both standard and domestic amount fields use the same `amount[]` name attribute
- The backend processes both fields identically
- No database schema changes required

## User Experience

### Workflow for Domestic Travel

1. **User selects travel-related expense head**
   - Travel fields appear automatically

2. **User selects "Domestic Travel"**
   - Amount field moves to appear after Distance field
   - KM field is hidden (not relevant for domestic travel)
   - Receipt upload becomes mandatory

3. **User clicks "Add Expense"**
   - New expense shows only travel details
   - Travel type is pre-selected as "domestic"
   - Amount field appears in travel section after Distance

### Visual Changes

- **Before**: Amount field appears before travel details
- **After**: For domestic travel, amount field appears after Distance field within travel section

## Testing

### Manual Testing Steps

1. **Test Amount Field Repositioning**
   - Navigate to new expense page
   - Select travel-related expense head
   - Select "Domestic Travel"
   - Verify amount field appears after Distance field
   - Verify standard amount field is hidden

2. **Test Travel-Only New Expenses**
   - Set first expense to domestic travel
   - Click "Add Expense" button
   - Verify new expense shows only travel fields
   - Verify travel type is pre-selected as "domestic"
   - Verify domestic amount field is visible

### Automated Testing

A test script `test_domestic_travel_enhancement.py` is provided for automated testing:
```bash
python test_domestic_travel_enhancement.py
```

## Browser Compatibility

- Tested on Chrome, Firefox, Safari, Edge
- Uses standard HTML5 and CSS3 features
- JavaScript uses jQuery (already included in project)

## Performance Impact

- Minimal performance impact
- No additional API calls
- Client-side JavaScript changes only
- No database queries affected

## Future Enhancements

Potential improvements for future versions:

1. **Travel Templates**: Save common travel routes for quick selection
2. **Auto-calculation**: Calculate amounts based on distance and rates
3. **Multi-city Support**: Support for complex multi-city travel itineraries
4. **Travel Policy Integration**: Automatic validation against company travel policies

## Troubleshooting

### Common Issues

1. **Amount field not appearing after Distance**
   - Check if travel type is set to "domestic"
   - Verify JavaScript console for errors
   - Ensure expense head is travel-related

2. **New expenses not showing travel fields**
   - Verify first expense has travel type set to "domestic"
   - Check if expense head is travel-related
   - Clear browser cache and reload

3. **Validation errors**
   - Ensure required fields are filled
   - Check that amount field is visible and filled
   - Verify receipt upload for domestic travel

### Debug Information

Enable browser developer tools to debug:
```javascript
// Check travel type value
console.log($('#travelType-1').val());

// Check if domestic amount field is visible
console.log($('#domestic-amount-row-1').is(':visible'));

// Check if standard amount field is hidden
console.log($('#standard-amount-row-1').is(':hidden'));
```

## Conclusion

This enhancement provides a more intuitive user experience for domestic travel expenses by:
- Positioning the amount field logically after distance information
- Automatically configuring new expenses for travel-only mode
- Maintaining consistency with existing validation and submission workflows

The implementation is backward compatible and requires no changes to existing expense submissions or database structure. 