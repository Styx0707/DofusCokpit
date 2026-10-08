on(construct){
   while(true)
   {
      if(!(0x366FC734 & 0x366FC734))
      {
         if(!ord("\x07"))
         {
            break;
         }
      }
      else
      {
         §§push(true);
      }
      var _temp_1 = §§pop();
      if(!(_temp_1 or _temp_1))
      {
         §§goto(addr0298);
      }
      break;
   }
   enabled = true;
   set("\x1a\x11\x11",false);
   selectable = true;
   styleName = "InventoryGrid";
   set("\x1b\x18\x02",5);
   §§push("\x1b\x18\x04");
   §§push(4);
   if(false)
   {
      setProperty(§§pop(), _X, §§pop());
   }
   else
   {
      addr0298:
      set(§§pop(),§§pop());
      §§goto(addr030f);
   }
   addr030f:
}
