# Copyright 2024 Muh. Rinaldi Ruslan

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style='dark')

@st.cache_data
def load_data():
    customers = pd.read_csv('E-Commerce Public Dataset/customers_dataset.csv')
    geolocation = pd.read_csv('E-Commerce Public Dataset/geolocation_dataset.csv')
    order_items = pd.read_csv('E-Commerce Public Dataset/order_items_dataset.csv')
    orders = pd.read_csv('E-Commerce Public Dataset/orders_dataset.csv')
    products = pd.read_csv('E-Commerce Public Dataset/products_dataset.csv')
    product_category_name_translation = pd.read_csv('E-Commerce Public Dataset/product_category_name_translation.csv')
    return customers, geolocation, order_items, orders, products, product_category_name_translation

customers, geolocation, order_items, orders, products, product_category_name_translation = load_data()

order_items = order_items.merge(products, on='product_id')
order_items = order_items.merge(product_category_name_translation, on='product_category_name', how='left')
orders = orders.merge(customers, on='customer_id')

orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders['order_approved_at'] = pd.to_datetime(orders['order_approved_at'])
orders['order_delivered_carrier_date'] = pd.to_datetime(orders['order_delivered_carrier_date'])
orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
orders['order_estimated_delivery_date'] = pd.to_datetime(orders['order_estimated_delivery_date'])

min_date = orders["order_approved_at"].min()
max_date = orders["order_approved_at"].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png", width=200) 
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

filtered_orders = orders[(orders["order_approved_at"] >= str(start_date)) & 
                        (orders["order_approved_at"] <= str(end_date))]

def main():
    st.title('Dashboard Analisis Data E-Commerce')

    st.header('Produk Terlaris dan Pendapatan Tertinggi')

    top_products = order_items.groupby('product_id').agg({'order_item_id': 'count', 'price': 'sum'}).reset_index()
    top_products = top_products.merge(products, on='product_id')
    top_products = top_products.merge(product_category_name_translation, on='product_category_name', how='left')
    top_products = top_products.sort_values(by='order_item_id', ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x='order_item_id', y='product_category_name_english', data=top_products, ax=ax)
    ax.set_title('Top 10 Produk Terlaris')
    ax.set_xlabel('Jumlah Terjual')
    ax.set_ylabel('Kategori Produk')
    st.pyplot(fig)

    top_revenue_products = top_products.sort_values(by='price', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x='price', y='product_category_name_english', data=top_revenue_products, ax=ax)
    ax.set_title('Top 10 Produk dengan Pendapatan Tertinggi')
    ax.set_xlabel('Pendapatan (BRL)')
    ax.set_ylabel('Kategori Produk')
    st.pyplot(fig)

    st.header('Tren Penjualan Bulanan')

    monthly_orders = filtered_orders.resample('ME', on='order_purchase_timestamp').size()

    fig, ax = plt.subplots(figsize=(12, 6))
    monthly_orders.plot(ax=ax)
    ax.set_title('Tren Penjualan Bulanan')
    ax.set_xlabel('Bulan')
    ax.set_ylabel('Jumlah Pesanan')
    st.pyplot(fig)

    st.header('Pola Musiman Penjualan')
    monthly_orders.index = monthly_orders.index.month
    monthly_avg_orders = monthly_orders.groupby(monthly_orders.index).mean()

    fig, ax = plt.subplots(figsize=(12, 6))
    monthly_avg_orders.plot(kind='bar', ax=ax)
    ax.set_title('Rata-rata Penjualan Bulanan')
    ax.set_xlabel('Bulan')
    ax.set_ylabel('Rata-rata Jumlah Pesanan')
    st.pyplot(fig)

    st.header('Kontribusi Penjualan per Negara Bagian')

    state_orders = filtered_orders['customer_state'].value_counts().reset_index()
    state_orders.columns = ['state', 'order_count']

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x='order_count', y='state', data=state_orders, ax=ax)
    ax.set_title('Kontribusi Penjualan per Negara Bagian')
    ax.set_xlabel('Jumlah Pesanan')
    ax.set_ylabel('Negara Bagian')
    st.pyplot(fig)

    st.header('Pelanggan dengan Pembelian Terbanyak')

    top_customers = filtered_orders.groupby('customer_unique_id').size().reset_index(name='order_count')
    top_customers = top_customers.sort_values(by='order_count', ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x='order_count', y='customer_unique_id', data=top_customers, ax=ax)
    ax.set_title('Top 10 Pelanggan dengan Pembelian Terbanyak')
    ax.set_xlabel('Jumlah Pesanan')
    ax.set_ylabel('ID Pelanggan')
    st.pyplot(fig)

    st.caption('Copyright (C) Muh. Rinaldi Ruslan 2023')

if __name__ == '__main__':
    main()