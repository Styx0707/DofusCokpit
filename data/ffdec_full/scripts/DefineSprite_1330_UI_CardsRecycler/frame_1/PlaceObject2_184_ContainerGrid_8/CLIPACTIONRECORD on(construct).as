on(construct){
   while(true)
   {
      if(!(0x2504203F | 0x2504203F))
      {
         if(!ord("\x04"))
         {
            break;
         }
      }
      else
      {
         §§push(false);
      }
      if(§§pop())
      {
         break;
      }
      enabled = true;
      set("\x1a\x11\x11",true);
      selectable = true;
      styleName = "InventoryGrid";
      set("\x1b\x18\x02",9);
      §§push("\x1b\x18\x04");
      §§push(3);
      if(false)
      {
         §§pop() implements ;
      }
      else
      {
         addr8947:
         set(§§pop(),§§pop());
      }
      return;
   }
   §§goto(addr8947);
}
