# Mobile Address Selection Fix

## Problem
On mobile devices, the native `<select>` dropdown showed addresses in a popup modal with Prev/Next buttons. The "Next" button wouldn't highlight after selecting an address because the JavaScript `change` event only fires after dismissing the native picker.

## Solution
Replaced the native `<select>` element with a custom, mobile-friendly address list that provides:

### Key Features
1. **Direct Selection**: Click/tap any address to select it immediately
2. **Visual Feedback**: Selected addresses are highlighted in purple with a radio button indicator
3. **Search Functionality**: Filter addresses by typing in the search box
4. **Mobile Optimized**: Touch-friendly with proper spacing and scrolling
5. **No Native Picker Issues**: Bypasses all mobile browser default behaviors

### Changes Made

#### HTML Structure
- Replaced `<select id="addressSelect">` with:
  ```html
  <div class="address-search">
    <input type="text" id="addressSearch" placeholder="🔍 Search addresses..." />
  </div>
  <div class="address-list" id="addressList">
    <!-- Addresses dynamically populated here -->
  </div>
  ```

#### JavaScript Functions
- **`populateAddresses()`**: Creates clickable address items instead of select options
- **`renderAddressList()`**: Renders filtered address list with radio button UI
- **`selectAddress(uprn)`**: Handles address selection and enables Continue button
- **`handleAddressSelect()`**: Simplified to use `selectedUPRN` variable
- **Search filtering**: Real-time address filtering as user types

#### CSS Styling
- `.address-list`: Scrollable container (400px max height, 350px on mobile)
- `.address-item`: Touch-friendly items with hover and selected states
- `.address-radio`: Custom radio button indicator
- `.address-search`: Search input styling
- Mobile-optimized spacing and font sizes

## Testing on Mobile

### Before Deployment
1. Test on Chrome DevTools mobile emulation
2. Check various screen sizes (iPhone SE, iPhone 12, iPad, Android)
3. Verify search works properly
4. Ensure scrolling works in address list
5. Test touch interactions

### After Deployment to Vercel
1. Test on actual iPhone (Safari)
2. Test on actual Android (Chrome)
3. Verify PWA functionality still works
4. Test address selection flow end-to-end

## Benefits
- ✅ No more native picker issues on mobile
- ✅ Immediate visual feedback when selecting
- ✅ Search functionality for long address lists
- ✅ Better UX with clear selection state
- ✅ Touch-optimized interface
- ✅ Consistent behavior across all browsers and devices

## Rollback Plan
If issues occur, the original select-based implementation can be restored by:
1. Reverting the HTML structure to use `<select>`
2. Restoring the original `populateAddresses()` function
3. Removing the custom CSS classes

## Notes
- All addresses are now stored in the `addresses` array globally
- The `selectedUPRN` variable tracks the current selection
- The Continue button is enabled immediately upon selection
- Search is case-insensitive and searches the full address string
