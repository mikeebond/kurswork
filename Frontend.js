

import React, { useState } from 'react';

const TransactionForm = () => {
  // Стан для збереження введених даних
  const [formData, setFormData] = useState({
    account_id: 1,
    category_id: 1,
    amount: '',
    description: ''
  });

  // Функція обробки відправки форми
  const handleSubmit = async (e) => {
    e.preventDefault(); // Запобігаємо перезавантаженню сторінки

    try {
      // Відправка POST-запиту на FastAPI сервер
      const response = await fetch('http://127.0.0.1:8000/api/transactions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          account_id: parseInt(formData.account_id),
          category_id: parseInt(formData.category_id),
          amount: parseFloat(formData.amount),
          description: formData.description
        }),
      });

      if (response.ok) {
        alert('Транзакцію успішно додано!');
        // Очищення форми після успішної відправки
        setFormData({...formData, amount: '', description: ''});
      } else {
        alert('Помилка при додаванні транзакції');
      }
    } catch (error) {
      console.error('Помилка мережі:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="transaction-form">
      <h3>Додати транзакцію</h3>

      <label>Сума:</label>
      <input
        type="number"
        value={formData.amount}
        onChange={(e) => setFormData({...formData, amount: e.target.value})}
        required
      />

      <label>Опис:</label>
      <input
        type="text"
        value={formData.description}
        onChange={(e) => setFormData({...formData, description: e.target.value})}
      />

      <button type="submit">Зберегти</button>
    </form>
  );
};

export default TransactionForm;