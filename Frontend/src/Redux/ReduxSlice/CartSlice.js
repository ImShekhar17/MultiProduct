import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    items: [],
    isOpen: false,
    totalAmount: 0,
    totalCount: 0,
};

const cartSlice = createSlice({
    name: 'cart',
    initialState,
    reducers: {
        toggleCart: (state) => {
            state.isOpen = !state.isOpen;
        },
        addToCart: (state, action) => {
            const existingItem = state.items.find(item => item.name === action.payload.name);
            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                state.items.push({ ...action.payload, quantity: 1 });
            }
            state.totalCount += 1;
            state.totalAmount += action.payload.price;
        },
        removeFromCart: (state, action) => {
            const index = state.items.findIndex(item => item.name === action.payload);
            if (index !== -1) {
                const item = state.items[index];
                state.totalCount -= item.quantity;
                state.totalAmount -= item.price * item.quantity;
                state.items.splice(index, 1);
            }
        },
        updateQuantity: (state, action) => {
            const { name, quantity } = action.payload;
            const item = state.items.find(item => item.name === name);
            if (item) {
                const diff = quantity - item.quantity;
                item.quantity = quantity;
                state.totalCount += diff;
                state.totalAmount += item.price * diff;
            }
        },
        clearCart: (state) => {
            state.items = [];
            state.totalAmount = 0;
            state.totalCount = 0;
        }
    },
});

export const { toggleCart, addToCart, removeFromCart, updateQuantity, clearCart } = cartSlice.actions;

export const selectCartItems = (state) => state.cart.items;
export const selectCartTotal = (state) => state.cart.totalAmount;
export const selectCartCount = (state) => state.cart.totalCount;
export const selectIsCartOpen = (state) => state.cart.isOpen;

export default cartSlice.reducer;
