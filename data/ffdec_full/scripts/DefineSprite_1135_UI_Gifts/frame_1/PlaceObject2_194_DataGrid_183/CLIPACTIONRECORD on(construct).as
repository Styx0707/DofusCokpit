on(construct){
   while(true)
   {
      if(false)
      {
         if(!(true or true))
         {
            break;
         }
      }
      else
      {
         §§push(false);
      }
      if(!§§pop())
      {
         cellRenderer = "GiftItem";
         enabled = false;
         multipleSelection = false;
         rowHeight = 80;
         §§push("styleName");
         §§push("LightBrownDataGrid");
         if(!getTimer())
         {
            §§goto(addr74e8);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   set("\x1b\x10\x18",0);
   addr74e8:
   getProperty(§§pop(), _X);
}
