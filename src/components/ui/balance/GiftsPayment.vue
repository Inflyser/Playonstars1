<template>

    <div class="icon-wrapper">
      <div class="circle-icon-container">
        <img src="@/assets/images/gift.svg" alt="Иконка" class="circle-icon" />
      </div>
    </div>
    <h3 style="text-align: center; color: white;">Пополнение подарками</h3>
    <p style="color: #A2A2A2; text-align: center; font-size: 14px; margin: 10px 20px 40px 20px;">
        Для пополнения баланса подарком отправьте
        подарок нашему боту @playstars
        После отправки подарок автоматически зачислится в ваш инвентарь по текущей рыночной цене
        Вы сможете продать подарок для открытия кейсов или вывести его обратно, если цена вас не устроила
    </p>
</template>





<style scoped>
.icon-wrapper {
  margin: 40px 0px 0px 0px;
  display: flex;
  justify-content: center; /* Центрирование по горизонтали */
  align-items: center;     /* Центрирование по вертикали */
  width: 100%;
  height: 100%;            /* Занимает всю высоту родителя */
}

.circle-icon {
  width: 70px;
  height: 70px;
  object-fit: contain;
}

</style>