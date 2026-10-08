on(construct){
   loop3:
   while(true)
   {
      loop4:
      while(true)
      {
         if(false)
         {
            if(false)
            {
               while(true)
               {
                  §§pop()[0] = 21;
                  eval("\x01")[1] = 94;
                  eval("\x01")[2] = 94;
                  §§push("\x01");
                  if(!ord("\x04"))
                  {
                     break;
                  }
                  §§goto(addr053c);
                  break loop4;
               }
               §§goto(addr04f9);
               addr04b2:
            }
         }
         else
         {
            §§push(419650132);
         }
         var _temp_1 = §§pop();
         if(!(_temp_1 & _temp_1))
         {
            break;
         }
         break loop3;
      }
      §§goto(addr04b2);
   }
   cellRenderer = "UI_BigStorePriceItemNoBuy";
   set("\x16\x1d\x1b",[]);
   eval("\x16\x1d\x1b")[0] = "";
   loop5:
   while(true)
   {
      loop6:
      while(true)
      {
         §§push(eval("\x16\x1d\x1b"));
         §§push(1);
         §§push("priceSet1");
         if(!getTimer())
         {
            §§push(getProperty(§§pop(), _X));
            while(true)
            {
               eval(§§pop())[3] = 94;
               set(§§constant(8),true);
               set(§§constant(9),false);
               set(§§constant(10),20);
               set(§§constant(11),§§constant(12));
               §§push(§§constant(13));
               §§push(20);
               break loop5;
               §§pop()[§§pop()] = §§pop();
               §§push(getProperty(§§pop(), _X));
            }
            §§goto(addr0679);
            addr053c:
         }
         while(true)
         {
            §§pop()[§§pop()] = §§pop();
            eval(§§constant(2))[2] = §§constant(5);
            eval(§§constant(2))[3] = §§constant(6);
            set(§§constant(7),[]);
            §§push(§§constant(7));
            break loop4;
            §§push(new §\§\§pop()§());
            continue loop6;
         }
         break loop4;
      }
      addr04f9:
      startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
      break;
   }
   set(§§pop(),§§pop());
   §§goto(addr0679);
   §§pop() extends §§pop();
   addr0679:
}
