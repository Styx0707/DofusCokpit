on(construct){
   while(true)
   {
      if(false)
      {
         if(!(true and true))
         {
            break;
         }
      }
      else
      {
         §§push("\t");
      }
      if(ord(§§pop()))
      {
         enabled = true;
         set("\x1a\x11\x11",true);
         selectable = true;
         styleName = "InventoryGrid";
         set("\x1b\x18\x02",8);
         §§push("\x1b\x18\x04");
         §§push(3);
         if(!(getTimer() + 1))
         {
            §§goto(addr95e5);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   addr95e5:
   getProperty(§§pop(), _X);
}
