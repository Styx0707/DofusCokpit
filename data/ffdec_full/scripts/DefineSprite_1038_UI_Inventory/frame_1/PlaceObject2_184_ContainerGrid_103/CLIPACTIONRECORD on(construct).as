on(construct){
   while(true)
   {
      if(!ord("\x02"))
      {
         if(!ord("\x02"))
         {
            break;
         }
      }
      else
      {
         §§push("\x0b");
      }
      if(ord(§§pop()))
      {
         enabled = true;
         set("\x1a\x11\x11",true);
         selectable = true;
         styleName = "InventoryGrid";
         §§push("\x1b\x18\x02");
         §§push(4);
         if(!ord("\x07"))
         {
            setProperty(§§pop(), _X, §§pop());
            §§goto(addr2f81);
         }
      }
      set(§§pop(),§§pop());
      §§push("\x1b\x18\x04");
      §§push(9);
      break;
   }
   set(§§pop(),§§pop());
   addr2f81:
}
