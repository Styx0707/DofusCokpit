on(construct){
   while(true)
   {
      if(false)
      {
         if(!(0x0F08AD70 & 0x0F08AD70))
         {
            break;
         }
      }
      else
      {
         §§push("\x07");
      }
      if(ord(§§pop()))
      {
         backgroundDown = "ButtonSquareDown";
         backgroundUp = "ButtonSquareUp";
         enabled = true;
         icon = "TreeDots";
         §§push("label");
         §§push("");
         if(!ord("\x07"))
         {
            §§goto(addr67e84);
         }
      }
      set(§§pop(),§§pop());
      selected = false;
      break;
   }
   styleName = "SmallSquareButton";
   toggle = false;
   addr67e84:
   getProperty(§§pop(), _X);
}
