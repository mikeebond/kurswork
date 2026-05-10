
// Модуль автоматизованого тестування (Jest + React Testing Library)

import { render, screen, fireEvent } from '@testing-library/react';
import TransactionForm from './TransactionForm';

describe('Тестування компонента TransactionForm', () => {

  test('перевірка наявності основних елементів форми на сторінці', () => {
    // Рендеримо компонент у віртуальному DOM
    render(<TransactionForm />);

    // Перевіряємо, чи відображається заголовок
    const headingElement = screen.getByText(/Додати транзакцію/i);
    expect(headingElement).toBeInTheDocument();

    // Перевіряємо наявність кнопки підтвердження
    const buttonElement = screen.getByRole('button', { name: /Зберегти/i });
    expect(buttonElement).toBeInTheDocument();
  });

  test('перевірка валідації та оновлення стану при введенні суми', () => {
    render(<TransactionForm />);

    // Знаходимо поле вводу для суми
    const amountInput = screen.getByLabelText(/Сума:/i);

    // Імітуємо введення суми транзакції користувачем
    fireEvent.change(amountInput, { target: { value: '1500' } });

    // Перевіряємо, чи змінилося значення поля (контрольований компонент)
    expect(amountInput.value).toBe('1500');
  });
});