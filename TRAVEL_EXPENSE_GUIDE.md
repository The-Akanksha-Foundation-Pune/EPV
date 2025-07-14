# Travel Expense Functionality Guide

## Overview

The EPV system now supports travel expenses with two types:
- **Local Travel**: For travel within the same city/area
- **Domestic Travel**: For travel between different cities/states

## Features

### Local Travel
- **Required Fields**: Date, From, To, Mode, KM, Amount
- **Receipt Upload**: 
  - Optional for Car/Bike
  - Mandatory for all other modes (Bus, Train, Flight, Taxi, Auto, Other)

### Domestic Travel
- **Required Fields**: Date, From, To, Mode, Amount
- **Receipt Upload**: Always mandatory regardless of mode

## How to Use

### 1. Database Setup
First, run the migration script to add travel columns to the database:

```bash
python add_travel_columns.py
```

### 2. Adding Travel Expense Heads
Make sure you have travel-related expense heads in your system:
- "Travel"
- "Local Travel" 
- "Domestic Travel"
- Or any expense head containing the word "travel"

### 3. Creating a Travel Expense

1. **Navigate to New Expense Form**
   - Go to the expense submission page

2. **Select Travel Expense Head**
   - Choose any expense head that contains "travel" in the name
   - Travel fields will automatically appear

3. **Fill Travel Details**
   - **Travel Type**: Select Local or Domestic
   - **Mode of Travel**: Choose from Car, Bike, Bus, Train, Flight, Taxi, Auto, Other
   - **From**: Enter source location
   - **To**: Enter destination location
   - **Travel Date**: Select the date of travel
   - **Distance (KM)**: Required for local travel only

4. **Upload Receipts**
   - **Local Travel with Car/Bike**: Receipt upload is optional
   - **Local Travel with other modes**: Receipt upload is mandatory
   - **Domestic Travel**: Receipt upload is always mandatory

5. **Submit the Expense**
   - The system will validate all required fields
   - Travel details will be included in the generated PDF

## Technical Implementation

### Database Changes
Added travel columns to `epv_item` table:
- `travel_type` (VARCHAR(20)): 'local' or 'domestic'
- `travel_mode` (VARCHAR(50)): Mode of transportation
- `travel_from` (VARCHAR(100)): Source location
- `travel_to` (VARCHAR(100)): Destination location
- `travel_date` (DATE): Travel date
- `travel_km` (FLOAT): Distance in kilometers (local travel only)

### Frontend Changes
- Dynamic form fields that appear when travel expense head is selected
- Real-time validation based on travel type and mode
- Conditional receipt upload requirements
- Smooth animations for better user experience

### Backend Changes
- Enhanced form processing to capture travel data
- Updated PDF generation to include travel details
- Validation logic for travel-specific requirements

### PDF Generation
Travel expenses will show an additional "Travel Details" column in the PDF with:
- Travel type and mode
- From/To locations
- Travel date
- Distance (for local travel)

## Validation Rules

### Local Travel
- All travel fields are required
- KM field is mandatory
- Receipt upload depends on mode:
  - Car/Bike: Optional
  - Others: Mandatory

### Domestic Travel
- All travel fields except KM are required
- KM field is hidden and not required
- Receipt upload is always mandatory

## Testing

Run the test script to verify functionality:

```bash
python test_travel_functionality.py
```

This will check:
- Database migration status
- Expense heads configuration
- PDF generation with travel data
- HTML template completeness

## Troubleshooting

### Common Issues

1. **Travel fields don't appear**
   - Ensure expense head contains "travel" in the name
   - Check browser console for JavaScript errors

2. **Validation errors**
   - Verify all required fields are filled
   - Check travel type and mode combinations

3. **PDF generation fails**
   - Ensure ReportLab is installed
   - Check file permissions for temporary directory

4. **Database errors**
   - Run the migration script: `python add_travel_columns.py`
   - Verify database connection settings

### Support

For technical issues, check:
- Application logs for error messages
- Database connection and permissions
- File upload directory permissions
- Browser console for JavaScript errors

## Future Enhancements

Potential improvements:
- Travel expense templates
- Automatic distance calculation
- Integration with mapping services
- Travel policy enforcement
- Bulk travel expense import
- Travel expense analytics and reporting 