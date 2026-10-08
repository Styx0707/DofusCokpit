on(construct){
   while(true)
   {
      if(!ord("\x02"))
      {
         if(!(0x301D1103 | 0x301D1103))
         {
            break;
         }
      }
      else
      {
         §§push("enabled");
         §§push(true);
      }
      set(§§pop(),§§pop());
      set("\x1a\x11\x11",false);
      §§push("selectable");
      §§push(false);
      break;
   }
   set(§§pop(),§§pop());
   styleName = "ExchangeGrid";
   set("\x1b\x18\x02",1);
   set("\x1b\x18\x04",1);
}
