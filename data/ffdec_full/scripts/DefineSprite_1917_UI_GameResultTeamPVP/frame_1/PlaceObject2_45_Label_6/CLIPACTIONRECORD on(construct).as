on(construct){
   while(true)
   {
      if(!(0x30B3FBA0 & 0x30B3FBA0))
      {
         if(!ord("\x0b"))
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
      html = false;
      multiline = false;
      styleName = "WhiteCenterSmallLabel";
      text = "";
      §§push("wordWrap");
      §§push(false);
      if(!getTimer())
      {
         §§goto(addr12d7f);
      }
      break;
   }
   set(§§pop(),§§pop());
   addr12d7f:
   getProperty(§§pop(), _X);
}
